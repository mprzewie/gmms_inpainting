# 2021-04-16 22:04:35.189264
python train_wae.py --experiment_name=wae_v9/inp_zero --convar_type=naive --inpainter_type=zero --batch_size 64 --dataset svhn --img_size 32 --mask_hidden_h 16 --mask_hidden_w 16 --num_epochs=10 --render_every 2 --dataset_root /mnt/users/mprzewiezlikowski/local/data/.data/ --lr 4e-4 --wae_recon_loss mse --wae_bl 2 --wae_depth 2 --max_benchmark_batches -1 --wae_latent_size 20 --wae_fc 96 --wae_lc 96 --wae_disc_loss_weight 0.01
