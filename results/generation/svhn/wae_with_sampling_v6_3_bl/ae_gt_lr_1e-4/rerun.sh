# 2021-04-12 19:26:53.802288
python train_wae.py --experiment_name=wae_with_sampling_v6_3_bl/ae_gt_lr_1e-4 --convar_type=naive --inpainter_type=gt --batch_size 64 --dataset svhn --img_size 32 --mask_hidden_h 16 --mask_hidden_w 16 --num_epochs=10 --render_every 2 --dataset_root /mnt/users/mprzewiezlikowski/local/data/.data/ --lr 4e-4 --wae_bl 3 --wae_recon_loss mse --max_benchmark_batches=-1 --skip_fid --lr 1e-4 --wae_disc_loss_weight 0
